#!/bin/bash

# Create CSV if it doesn't exist
if [ ! -f "trained_stocks.csv" ]; then
    echo "symbol,sector,trained_date,epochs" > trained_stocks.csv
fi

# Top 100 most traded stocks (by market cap and volume)
stocks=(
    # Biotech / Pharma (event-driven, volatile)
    "SRPT" "NVAX" "ICPT" "BCRX" "SAVA" "IMVT" "MRNS" "ADMA" "INSM" "BLUE"
    "ALLO" "CRSP" "EDIT" "BEAM" "RNA" "ACHC" "KURA" "XENE" "FATE" "RETA"

    # Small/Mid-Cap Tech / AI / Cloud
    "AI" "UPST" "PLTR" "BIGC" "ZI" "SOUN" "BILL" "PD" "DDOG" "VERI"
    "MQ" "AMPL" "ASAN" "COIN" "AFRM" "WIX" "RBLX" "HOOD" "DUOL" "TSP"

    # Renewable / EV / Green Tech
    "BLNK" "CHPT" "ENVX" "QS" "RUN" "SPWR" "PLUG" "FCEL" "FSLR" "NOVA"
    "AY" "MAXN" "ENPH" "ARRY" "EVGO" "BE" "STEM" "TPIC" "CWEN" "NEO"

    # Meme Stocks / Retail-driven
    "GME" "AMC" "BB" "TLRY" "SNDL" "NIO" "XPEV" "LCID" "RIVN"
    "DWAC" "SOFI" "BARK" "OSTK" "SKLZ" "OPEN" "VRM" "BBIG" "CLSK" "RIOT"

    # China / International ADRs
    "JD" "BABA" "PDD" "TCEHY" "NIO" "XPEV" "LI" "YMM" "DIDIY" "ZTO"
    "KWEB" "IQ" "HUYA" "TAL" "EDU" "WB" "BIDU" "NTES" "VIPS"
)

# Train each stock
for stock in "${stocks[@]}"
do
    # Check if stock is already in CSV
    if grep -q "^$stock," trained_stocks.csv; then
        echo "Skipping $stock - already trained"
        continue
    fi
    
    echo "Training model for $stock..."
    if python3 train.py --symbol "$stock" --epochs 200; then
        # Add successful training to CSV with appropriate sector
        sector="Other"  # Default sector
        case $stock in
            SRPT|NVAX|ICPT|BCRX|SAVA|IMVT|MRNS|ADMA|INSM|BLUE|ALLO|CRSP|EDIT|BEAM|RNA|ACHC|KURA|XENE|FATE|RETA)
                sector="Biotech";;
            AI|UPST|PLTR|BIGC|ZI|SOUN|BILL|PD|DDOG|VERI|MQ|AMPL|ASAN|COIN|AFRM|WIX|RBLX|HOOD|DUOL|TSP)
                sector="Tech";;
            BLNK|CHPT|ENVX|QS|RUN|SPWR|PLUG|FCEL|FSLR|NOVA|AY|MAXN|ENPH|ARRY|EVGO|BE|STEM|TPIC|CWEN|NEO)
                sector="Green";;
            GME|AMC|BB|TLRY|SNDL|NIO|XPEV|LCID|RIVN|DWAC|SOFI|BARK|OSTK|SKLZ|OPEN|VRM|BBIG|CLSK|RIOT)
                sector="Retail";;
            JD|BABA|PDD|TCEHY|NIO|XPEV|LI|YMM|DIDIY|ZTO|KWEB|IQ|HUYA|TAL|EDU|WB|BIDU|NTES|VIPS)
                sector="China";;
        esac
        echo "$stock,$sector,$(date '+%Y-%m-%d'),200" >> trained_stocks.csv
        echo "Completed training for $stock"
    else
        echo "Failed to train $stock"
    fi
    echo "------------------------"
done
